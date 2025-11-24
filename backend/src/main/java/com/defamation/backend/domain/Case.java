package com.defamation.backend.domain;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "cases")
@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Case {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name="raw_id", nullable=false, unique=true)
    private Long rawId;

    @Lob
    @Column(name="problem_situation", nullable=false, columnDefinition="LONGTEXT")
    private String problemSituation;

    // TEXT 컬럼에 JSON 문자열로 저장된 상태
    @Lob
    @Column(name="participants", nullable=false, columnDefinition="TEXT")
    private String participants;

    @Lob
    @Column(name="case_names", nullable=false, columnDefinition="TEXT")
    private String caseNames;

    @Column(name="case_type", nullable=false)
    private String caseType;

    @Column(name="court_level", nullable=false)
    private Integer courtLevel;

    @Column(name="defendant")
    private String defendant;

    @Column(name="label", nullable=false)
    private Integer label;

    // 형량(flatten) - 학습 데이터용
    @Column(name="sentence_type")
    private String sentenceType;

    @Column(name="sentence_value")
    private String sentenceValue;

    @Column(name="sentence_suspension")
    private String sentenceSuspension;

    @Lob
    @Column(name="sentence_additional_order", columnDefinition="LONGTEXT")
    private String sentenceAdditionalOrder;

    @Lob
    @Column(name="sentence_reason", columnDefinition="LONGTEXT")
    private String sentenceReason;

    @Column(name="sentence_judgment")
    private String sentenceJudgment;

    @Builder.Default
    @Column(name="is_deleted", nullable=false)
    private Boolean isDeleted = false;

    @Column(name="created_at", insertable=false, updatable=false)
    private LocalDateTime createdAt;
}
